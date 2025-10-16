<template>
  <div class="payment-switcher">
    <nav class="nav nav-pills justify-content-center">
      <div v-if="hasUpn && !recurring" class="nav-item">
        <button
          :class="['nav-link', { active: active === 'upn' }]"
          type="button"
          @click="changeActive('upn')"
        >
          {{ $t("payment.depositSlip") }}
        </button>
      </div>
      <div v-if="hasFlik && !recurring" class="nav-item">
        <button
          :class="['nav-link', { active: active === 'flik' }]"
          type="button"
          @click="changeActive('flik')"
        >
          {{ $t("payment.flik") }}
        </button>
      </div>
      <div class="nav-item">
        <button
          :class="['nav-link', { active: active === 'card' }]"
          type="button"
          @click="changeActive('card')"
        >
          {{ $t("payment.card") }}
        </button>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: "PaymentSwitcher",
  props: {
    recurring: {
      type: Boolean,
      default: false,
    },
    hasUpn: {
      type: Boolean,
      default: true,
    },
    hasFlik: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["change"],
  data() {
    return {
      active: "upn",
    };
  },
  mounted() {
    this.$emit("change", this.active);
  },
  methods: {
    changeActive(newActive) {
      if (this.active === newActive) {
        return;
      }
      this.active = newActive;
      this.$emit("change", newActive);
    },
  },
};
</script>

<style lang="scss" scoped>
.payment-switcher {
  margin-bottom: 1.5rem;

  .nav {
    // margin: 0 #{-$content-mobile-padding};

    .nav-item {
      position: relative;
      margin: 0 0.5rem;

      &:not(:first-child)::before {
        content: "";
        background-color: #333;
        display: block;
        width: 1px;
        position: absolute;
        top: -0.25rem;
        bottom: -0.25rem;
        left: -0.5rem;
      }

      .nav-link {
        border-radius: 4px;
        border: 0;
        background: transparent;
        color: #333;
        text-transform: uppercase;
        font-weight: 300;

        &.active {
          background-color: rgba($color: #000000, $alpha: 0.3);
        }

        &:focus {
          box-shadow: none;
        }
      }
    }
  }
}
.hudapobuda.payment-switcher {
  .nav .nav-item .nav-link {
    border-radius: 0;
    font-size: 0.825rem;
    padding: 0.5rem;
    @media (min-width: 360px) {
      font-size: 1rem;
      padding: 0.5rem 1rem;
    }
    &.active {
      background-color: #f4b7d1;
    }
  }
}
</style>
