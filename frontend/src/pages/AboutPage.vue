<template>
  <div class="about-page w-full h-full bg-white flex flex-column overflow-hidden">
    <!-- Header -->
    <div class="header p-4 border-bottom-1 border-200 bg-white">
        <h1 class="text-2xl font-bold m-0 text-900">關於平台 (About System)</h1>
        <p class="text-600 m-0 mt-1">System Overview & Documentation</p>
    </div>

    <!-- Content -->
    <div class="content-container flex-1 overflow-y-auto p-5">
        <div v-if="loading" class="flex flex-column align-items-center justify-content-center h-full">
            <i class="pi pi-spin pi-spinner text-4xl text-primary mb-3"></i>
            <span class="text-gray-500">Loading documentation...</span>
        </div>

        <div v-else-if="error" class="flex flex-column align-items-center justify-content-center h-full text-red-500">
            <i class="pi pi-exclamation-circle text-4xl mb-3"></i>
            <span>{{ error }}</span>
        </div>

        <div v-else class="markdown-body max-w-50rem mx-auto pb-6" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import apiClient from '../api/client';
import { marked } from 'marked';

const loading = ref(true);
const content = ref('');
const error = ref('');

const renderedContent = computed(() => {
    return marked.parse(content.value);
});

onMounted(async () => {
    try {
        const res = await apiClient.get('/system/readme');
        // apiClient interceptor returns response.data directly
        content.value = (res as any).content;
    } catch (e: any) {
        console.error("Failed to load README", e);
        error.value = "Failed to load documentation. Please try again later.";
    } finally {
        loading.value = false;
    }
});
</script>

<style>
/* Reusing markdown styles from ChatbotPage or defining localized ones */
.markdown-body {
    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
    font-size: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    color: #24292f;
}

.markdown-body h1 {
    font-size: 2em;
    padding-bottom: .3em;
    border-bottom: 1px solid #d0d7de;
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
}

.markdown-body h2 {
    font-size: 1.5em;
    padding-bottom: .3em;
    border-bottom: 1px solid #d0d7de;
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
}

.markdown-body h3 {
    font-size: 1.25em;
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
}

.markdown-body p {
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body ul, .markdown-body ol {
    padding-left: 2em;
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body blockquote {
    padding: 0 1em;
    color: #57606a;
    border-left: .25em solid #d0d7de;
    margin: 0;
    margin-bottom: 16px;
}

.markdown-body code {
    padding: .2em .4em;
    margin: 0;
    font-size: 85%;
    white-space: break-spaces;
    background-color: rgba(175,184,193,0.2);
    border-radius: 6px;
    font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
}

.markdown-body pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: #f6f8fa;
    border-radius: 6px;
    margin-bottom: 16px;
}

.markdown-body pre code {
    padding: 0;
    background-color: transparent;
}

.markdown-body table {
    border-spacing: 0;
    border-collapse: collapse;
    margin-top: 0;
    margin-bottom: 16px;
    width: 100%;
}

.markdown-body table th,
.markdown-body table td {
    padding: 6px 13px;
    border: 1px solid #d0d7de;
}

.markdown-body table th {
    font-weight: 600;
    background-color: #f6f8fa;
}

.markdown-body table tr:nth-child(2n) {
    background-color: #f6f8fa;
}

.markdown-body hr {
    height: .25em;
    padding: 0;
    margin: 24px 0;
    background-color: #d0d7de;
    border: 0;
}
</style>
