<template>
  <div class="language-terminal ext-terminal">
    <button
      class="copy"
      :class="{ copied: copied }"
      title="Copy Code"
      @click.stop="copyText">
    </button>
    <span class="lang">terminal</span>
    <pre class="shiki vp-code" tabindex="0"><code class="term" ref="codeRef"><slot></slot></code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const codeRef = ref<HTMLElement>(),
  copied = ref(false);

async function copyText() {
  if (!codeRef.value) {
    return;
  }

  let text = codeRef.value.textContent.replace(/\n\n/g, '\n');

  try {
    await navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  } catch (error) {
    console.error("Failed to copy", error);
  }
}
</script>
