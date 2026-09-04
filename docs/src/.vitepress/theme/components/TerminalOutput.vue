<template>
  <div class="language-terminal ext-terminal" ref="containerRef">
    <button
      class="copy"
      :class="{ copied: copied }"
      title="Copy Code"
      @click.stop="copyText"></button>
    <span class="lang">terminal</span>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const containerRef = ref<HTMLElement>();
const copied = ref(false);

async function copyText() {
  const codeEl = containerRef.value?.querySelector('code');
  if (!codeEl) {
    return;
  }

  try {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = codeEl.innerHTML.replace(/<br\s*\/?>/gi, '\n');

    await navigator.clipboard.writeText((tempDiv.textContent || '').replace(/\u00a0/g, ' '));

    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch (error) {
    // oxlint-disable-next-line no-console
    console.error('Failed to copy', error);
  }
}
</script>
