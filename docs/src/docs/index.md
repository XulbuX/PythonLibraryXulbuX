---
layout: false
---

<div style="padding: 2rem; text-align: center; font-family: sans-serif;">
  Redirecting to the <a :href="firstLink">documentation</a>...
</div>

<script setup>
import { useData, useRouter } from 'vitepress';
import { onMounted } from 'vue';

const { theme } = useData();
const router = useRouter();

// Get the first link from the sidebar dynamically:
const firstLink = theme.value.sidebar?.[0]?.items?.[0]?.link || '/';

onMounted(() => {
  // Client-side redirect:
  if (typeof window !== 'undefined') {
    router.go(firstLink);
  }
})
</script>
