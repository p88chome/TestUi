# 必須 import 所有繼承 Base 的 Model，
# 讓 Base.metadata.create_all 在啟動時能建出每一張表。
from .domain import Component, Workflow, RunExecution, EndpointType, RunStatus, AIModel
from .skill import Skill, SkillType, SkillExecution
from .task import TaskPackage
from .user import User
from .stats import UsageLog
from .news import PlatformNews
from .chat import ChatSession, ChatMessage
from .feedback import Feedback
from .assistant import Assistant
