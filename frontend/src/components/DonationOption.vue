<template>
  <button
    :class="[
      'donation-option',
      {
        'donation-option--selected': isSelected,
        'donation-option--amount-only': amountOnly,
      },
    ]"
    type="button"
    @click.prevent="onClick"
  >
    <div class="donation-option__content-wrapper">
      <div class="donation-option__content">
        <div class="donation-option__amount">
          <div v-if="donationPreset.custom" class="custom-amount">
            <!-- eslint-disable vue/no-mutating-props -->
            <input
              id="custom-amount"
              v-model="donationPreset.amount"
              type="number"
              min="1"
              class="form-control"
              @input="onClick"
            />
            <!-- eslint-enable vue/no-mutating-props -->
            <label for="custom-amount">€</label>
          </div>
          <span v-else>{{ donationPreset.amount }} €</span>
        </div>
        <div class="donation-option__description">
          {{ donationPreset.description }}
        </div>
      </div>
      <div :class="['donation-option__icon', { 'amount-only': amountOnly }]">
        <div class="icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="-2 -2 95 95"
            fill="none"
            stroke="currentColor"
            stroke-width="6"
          >
            <path
              class="circle"
              d="M47.9 1.6a44.3 44.3 0 100 88.5 44.3 44.3 0 000-88.5z"
            />
            <path
              class="checkmark"
              d="M72.9 35.7L40 68.7a1.4 1.4 0 01-2 0L18.6 49a1.4 1.4 0 010-2l6.8-6.8c.3-.2.6-.4 1-.4s.7.2 1 .5L39.2 52l25-25c.6-.6 1.4-.6 2 0l6.8 6.8a1.4 1.4 0 010 2z"
            />
          </svg>
        </div>
      </div>
    </div>
  </button>
</template>

<script>
export default {
  props: {
    donationPreset: {
      type: Object,
      required: true,
    },
    amountOnly: {
      type: Boolean,
      default: false,
    },
    isSelected: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    onClick(event) {
      this.$store.commit("setChosenAmount", this.donationPreset.amount);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.donation-option {
  display: flex;
  border: 0;
  padding: 0;
  margin-bottom: 1.5rem;
  width: 100%;

  &:focus {
    border: 0 !important;
    outline: none !important;
    box-shadow: none !important;

    .donation-option__content-wrapper {
      border: 2px solid $color;
      box-shadow: 0 0 0 0.2rem rgba($color, 0.25);
    }
  }

  &.donation-option--selected {
    .donation-option__content-wrapper {
      border: 2px solid $color;
    }

    path.circle {
      fill: #333;
      stroke-width: 0;
    }
    path.checkmark {
      fill: #FFFFFF;
      stroke-width: 0;
    }
  }

  &.donation-option--amount-only {
    .donation-option__content {
      display: flex;
      align-items: center;

      .donation-option__description {
        display: none;
      }
    }
  }

  .donation-option__content-wrapper {
    display: flex;
    align-items: stretch;
    width: 100%;
    height: 100%;
    padding: 1rem 1.25rem;
    text-align: left;
    border: 2px solid transparent;

    @include media-breakpoint-up(md) {
      padding: 1.5rem;
      flex-direction: column;
    }

    .donation-option__content {
      flex: 1;

      .donation-option__amount {
        font-size: 2rem;
        font-weight: 600;
        line-height: 1;

        @include media-breakpoint-up(md) {
          font-size: 2.25rem;
          margin-bottom: 1.25rem;
        }

        .custom-amount {
          margin-top: 0.5rem;
          position: relative;
          width: 75%;

          .form-control {
            background-color: transparent;
            font-size: 1.75rem;
            font-weight: 600;
            font-style: normal;
            color: inherit;
            padding-right: 1.75rem;
          }

          label {
            position: absolute;
            top: 0.7rem;
            right: 0.5rem;
            font-size: 2rem;
          }
        }
      }

      .donation-option__description {
        font-size: 1rem;
        font-weight: 300;
        font-style: italic;
        margin-top: 0.5rem;

        @include media-breakpoint-up(md) {
          font-size: 1.25rem;
        }
      }
    }

    .donation-option__icon {
      display: flex;
      align-items: center;

      &:not(.amount-only) {
        @include media-breakpoint-up(md) {
          flex-direction: column;
          align-items: flex-end;
          margin: 1rem -0.75rem -0.75rem -0.75rem;
        }
      }

      .icon {
        width: 2.5rem;
        color: #333;

        @include media-breakpoint-up(md) {
          width: 3rem;
        }

        svg {
          width: 100%;
          height: 100%;
        }
      }
    }
  }
}
</style>
