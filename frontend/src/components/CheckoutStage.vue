<template>
  <div :class="[
      'checkout-stage',
    ]">
    <div class="checkout-stage__container">
      <div class="checkout-stage__header">
        <slot name="header">
          <h1 class="checkout-stage__title">
            <slot name="title" />
          </h1>
        </slot>
      </div>
      <div class="checkout-stage__content">
        <slot name="content" />
      </div>
      <div class="checkout-stage__footer">
        <slot name="footer" />
      </div>
    </div>
    <div v-if="showTerms" class="checkout-stage__terms">
      <a href="https://danesjenovdan.si/pogoji" target="_blank">
        {{ $t('checkoutStage.terms') }}
      </a>
    </div>
    <div v-if="showDjndFooter" class="checkout-stage__footer_djnd">
      <hr />
      <div>
        <img src="../assets/logo-djnd.png" class="logo-djnd" alt="" />
        <a href="https://danesjenovdan.si/" target="_blank">
          {{ $t('checkoutStage.djndWebsite') }} <span class="icon-arrow-right">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="30 18 110.9 40" fill="#333333">
              <path
                d="M140.9 38a3 3 0 00-.9-2l-16-17c-1-1-3.1-1.4-4.3-.3-1.2 1-1.2 3.2 0 4.4L131 35H30v6h101l-11.3 12c-1 1-1.2 3.2 0 4.3 1.2 1 3.3.8 4.3-.2l16-17c.6-.6.9-1.3.9-2.1z" />
            </svg>
          </span>
        </a>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  props: {
    noHeader: {
      type: Boolean,
      default: false,
    },
    showTerms: {
      type: Boolean,
      default: false,
    },
    showDjndFooter: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout-stage {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  .checkout-stage__container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex: 1;

    .checkout-stage__content {
      display: flex;
      flex-direction: column;
      // flex: 1;
      // margin-bottom: auto;
      min-height: 21rem;

      @include media-breakpoint-up(md) {
        // margin-bottom: 0;
      }
    }

    .checkout-stage__header,
    .checkout-stage__footer {
      margin: 1.5rem 0;

      @include media-breakpoint-up(md) {
        margin: 2rem 0;
      }

      &:empty {
        display: none;
      }
    }

    .checkout-stage__header {
      .checkout-stage__title {
        margin: 0;
        font-size: 1.75rem;
        text-align: center;
        font-weight: 600;

        @include media-breakpoint-up(md) {
          font-size: 3rem;
        }
      }
    }
  }

  .checkout-stage__terms {
    margin-bottom: 1rem;
    text-align: center;

    a {
      color: inherit;
      font-size: 1rem;
      font-weight: 300;
      font-style: italic;
      text-decoration: underline;

      @include media-breakpoint-up(md) {
        font-size: 1.25rem;
      }

      &:hover {
        text-decoration: none;
      }
    }
  }

  .checkout-stage__footer_djnd {
    &>div {
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 1rem 0;
    }

    .logo-djnd {
      width: 140px;
      margin: 10px 40px;
    }

    a {
      color: #333333;
      font-weight: 300;
      font-size: 1.25rem;
    }

    a:hover {
      text-decoration: none;
    }

    .icon-arrow-right svg {
      width: 1.5em;
      margin: 0 5px;
    }
  }
}
</style>
