<template>
  <dynamic-link
    :class="[
      'confirm-button',
      {
        'confirm-button--block': block,
        'confirm-button--arrow': arrow,
        'confirm-button--hearts': hearts,
        loading: loading,
        disabled: disabled || loading,
      },
    ]"
    :disabled="disabled || loading"
  >
    <div v-if="loading" class="loader-container">
      <div class="lds-dual-ring" />
    </div>
    <div v-if="arrow" class="arrow">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="30 18 110.9 40"
        fill="#fff"
      >
        <path
          d="M140.9 38a3 3 0 00-.9-2l-16-17c-1-1-3.1-1.4-4.3-.3-1.2 1-1.2 3.2 0 4.4L131 35H30v6h101l-11.3 12c-1 1-1.2 3.2 0 4.3 1.2 1 3.3.8 4.3-.2l16-17c.6-.6.9-1.3.9-2.1z"
        />
      </svg>
    </div>
    <span class="text" v-text="text" />
    <div v-if="hearts" class="hearts">
      <div v-for="i in 3" :key="i" class="heart">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="8 0 92 100"
          fill="#fff"
        >
          <path
            d="M31.756 16.033c-5.075 0-10.122 2.005-13.969 6.031-7.693 8.051-7.715 20.974-.03 29.031l30.78 32.282c.746.787 2.162.787 2.907 0 10.268-10.746 20.513-21.504 30.781-32.25 7.693-8.052 7.693-20.98 0-29.032-7.694-8.051-20.275-8.051-27.969 0l-4.25 4.407-4.25-4.438c-4.147-4.357-9.286-6.052-14-6.031zm0 3.937c3.999 0 8.019 1.625 11.125 4.875l5.687 5.97c.746.787 2.162.787 2.907 0l5.656-5.938c6.212-6.502 16.007-6.501 22.219 0 6.212 6.5 6.212 16.999 0 23.5C69.57 58.61 59.786 68.86 50.006 79.095l-29.344-30.75c-6.207-6.509-6.212-16.999 0-23.5 3.106-3.25 7.095-4.875 11.094-4.875z"
          />
          <path
            fill="transparent"
            d="M 37.342652,67.767099 C 18.090047,46.826364 18.134724,46.877597 16.973735,44.409678 c -1.344773,-2.85859 -1.920544,-5.305628 -1.915189,-8.139595 0.0086,-4.56069 1.508983,-8.704631 4.317498,-11.924728 3.302805,-3.786823 6.989467,-5.546676 11.61956,-5.546676 5.242144,0 7.873474,1.476455 13.852388,7.772658 3.348548,3.526253 4.10063,4.173099 4.851999,4.173099 0.749401,0 1.611575,-0.735442 5.483968,-4.677862 4.822118,-4.909325 6.28592,-5.976108 9.328474,-6.798363 5.302958,-1.433133 10.830326,0.210955 14.897861,4.431292 2.249881,2.334398 3.625629,4.861192 4.435424,8.146396 1.06796,4.332548 0.507725,9.059656 -1.549861,13.077342 C 81.742592,46.003554 80.187686,48.058365 78.6601,49.7279 77.19211,51.332301 70.230527,58.916512 63.189912,66.581706 56.1493,74.246899 50.243163,80.683736 50.065167,80.885788 49.821604,81.162266 46.674044,77.916694 37.342652,67.767099 Z"
          />
        </svg>
      </div>
    </div>
  </dynamic-link>
</template>

<script>
import DynamicLink from "./DynamicLink.vue";

export default {
  components: {
    DynamicLink,
  },
  props: {
    text: {
      type: String,
      required: true,
    },
    block: {
      type: Boolean,
      default: false,
    },
    arrow: {
      type: Boolean,
      default: false,
    },
    hearts: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {};
  },
  methods: {},
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

@keyframes hearts-animation {
  0% {
    fill: transparent;
  }
  50% {
    fill: transparent;
  }
  51% {
    fill: #fff;
  }
  100% {
    fill: #fff;
  }
}

.confirm-button {
  display: inline-flex;
  align-items: center;
  padding: 1.3rem 3.2rem;
  font-size: 1.25rem;
  font-style: italic;
  font-weight: 600;
  font-family: "acumin-pro", sans-serif;
  letter-spacing: 0.125em;
  line-height: 1;
  color: black;
  background-color: rgba(black, 0.25);
  text-decoration: none;
  transition: background-color 0.15s;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
  transition: all 0.15s ease;

  // @include media-breakpoint-up(md) {
  //   font-size: 3rem;
  // }

  &:hover {
    transform: scale(0.95);

    .heart svg path:nth-child(2) {
      animation-name: hearts-animation;
      animation-duration: 600ms;
      animation-iteration-count: infinite;
    }

    .heart:nth-child(1) svg path:nth-child(2) {
      animation-delay: -300ms;
    }

    .heart:nth-child(2) svg path:nth-child(2) {
      animation-delay: -200ms;
    }

    .heart:nth-child(3) svg path:nth-child(2) {
      animation-delay: -100ms;
    }
  }

  &.loading {
    .text,
    .arrow,
    .hearts {
      opacity: 0;
    }
  }

  .loader-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: center;
    align-items: center;

    .lds-dual-ring {
      color: #fff;

      &,
      &::after {
        width: 2rem;
        height: 2rem;

        // @include media-breakpoint-up(md) {
        //   width: 3rem;
        //   height: 3rem;
        // }
      }
    }
  }

  .text {
    flex: 1;
    position: relative;
    top: 0.1em;
    letter-spacing: 1px;
    text-align: center;
    color: #ffffff;
  }

  .arrow {
    margin: -1em 0.5rem -1em -3.5rem;
    display: flex;
    height: 1.125em;

    // @include media-breakpoint-up(md) {
    //   height: 0.75em;
    // }

    svg {
      height: 100%;
    }
  }

  .hearts {
    margin: -1em -2.5rem -1em 0.5rem;

    .heart {
      height: 1.75em;
      display: inline-block;

      // @include media-breakpoint-up(md) {
      //   height: 1.25em;
      // }

      svg {
        height: 100%;
      }

      &.empty {
        display: none;
      }
    }
  }

  &.disabled,
  &:disabled {
    pointer-events: none;
    cursor: not-allowed;
    opacity: 0.6;
  }

  &.confirm-button--arrow {
    padding-right: 2rem;
  }

  &.confirm-button--hearts {
    padding-right: 3.2rem;
  }

  &.confirm-button--block {
    width: 100%;
  }
}
</style>
