<template>
  <div class="ext-attached-code">
    <span class="attached-title" v-if="title">{{ title }}</span>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title?: string }>();
</script>
