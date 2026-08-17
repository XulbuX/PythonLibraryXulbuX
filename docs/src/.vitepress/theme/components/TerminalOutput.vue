<template>
  <div class="language-terminal ext-terminal">
    <button
      class="copy"
      :class="{ copied: copied }"
      title="Copy Code"
      @click.stop="copyText"></button>
    <span class="lang">terminal</span>
    <pre class="shiki vp-code" tabindex="0"><code class="term" ref="codeRef"><slot /></code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const codeRef = ref<HTMLElement>();
const copied = ref(false);

async function copyText() {
  if (!codeRef.value) {
    return;
  }

  try {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = codeRef.value.innerHTML.replace(/<br\s*\/?>/gi, '\n');

    await navigator.clipboard.writeText(tempDiv.textContent || '');

    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch (error) {
    // oxlint-disable-next-line no-console
    console.error('Failed to copy', error);
  }
}
</script>
