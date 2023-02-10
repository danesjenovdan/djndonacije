<template>
  <router-link
    v-if="shouldUseNuxtLink"
    :to="to"
    @click=onClick
  >
    <slot />
  </router-link>
  <!-- eslint-disable-next-line vue/valid-template-root -->
  <a
    v-else
    :href="to"
    :target="isLinkExternal ? '_blank' : null"
    :rel="isLinkExternal ? 'noopener noreferrer' : null"
    @click=onClick
  >
    <slot />
  </a>
</template>

<script>
export default {
  props: {
    to: {
      type: String,
      default: '',
    },
  },
  computed: {
    isLinkEmpty() {
      return !this.to || this.to === '#';
    },
    isLinkExternal() {
      return !this.isLinkEmpty && /^https?:\/\//.test(this.to);
    },
    shouldUseNuxtLink() {
      return !this.isLinkEmpty && !this.isLinkExternal;
    },
  },
  methods: {
    onClick(event) {
      if (this.isLinkEmpty) {
        event.preventDefault();
      }
      // this.$emit('click', event);
    },
  },
};
</script>
