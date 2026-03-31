"""
Async Task Manager
簡易版非同步任務管理：使用 asyncio + 記憶體 dict 追蹤背景任務狀態。
未來可無痛替換為 Celery + Redis。

Usage:
    from app.services.task_manager import task_manager

    # 提交任務
    task_id = await task_manager.submit(my_coroutine(args))

    # 查詢狀態
    status = task_manager.get_status(task_id)
    # -> {"task_id": "xxx", "status": "running|completed|failed", "result": ..., "error": ...}
"""

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskInfo:
    """單一任務的狀態資訊"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """
    記憶體版非同步任務管理器。

    限制：
    - 任務狀態存在記憶體中，重啟後丟失
    - 適合中短期任務（< 30 分鐘）
    - 未來可替換為 Celery backend
    """

    def __init__(self, max_tasks: int = 100):
        self._tasks: Dict[str, TaskInfo] = {}
        self._max_tasks = max_tasks

    async def submit(self, coroutine) -> str:
        """
        提交一個 coroutine 作為背景任務。
        回傳 task_id。
        """
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id)

        # 清理舊任務（簡單的 LRU）
        if len(self._tasks) >= self._max_tasks:
            self._cleanup_old_tasks()

        self._tasks[task_id] = task_info

        # 建立背景 asyncio task
        asyncio.create_task(self._run_task(task_id, coroutine))
        logger.info(f"Task submitted: {task_id}")
        return task_id

    async def _run_task(self, task_id: str, coroutine):
        """執行任務並更新狀態"""
        task_info = self._tasks.get(task_id)
        if not task_info:
            return

        task_info.status = TaskStatus.RUNNING

        try:
            result = await coroutine
            task_info.status = TaskStatus.COMPLETED
            task_info.result = result
            logger.info(f"Task completed: {task_id}")
        except Exception as e:
            task_info.status = TaskStatus.FAILED
            task_info.error = str(e)
            logger.error(f"Task failed: {task_id} - {e}")
        finally:
            task_info.completed_at = datetime.utcnow()

    def get_status(self, task_id: str) -> Optional[Dict]:
        """查詢任務狀態"""
        task_info = self._tasks.get(task_id)
        if not task_info:
            return None
        return task_info.to_dict()

    def _cleanup_old_tasks(self):
        """清理已完成且最舊的任務"""
        completed = [
            (tid, info)
            for tid, info in self._tasks.items()
            if info.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
        ]
        # 按建立時間排序，刪除最舊的一半
        completed.sort(key=lambda x: x[1].created_at)
        for tid, _ in completed[: len(completed) // 2 + 1]:
            del self._tasks[tid]


# 全域單例
task_manager = TaskManager()
