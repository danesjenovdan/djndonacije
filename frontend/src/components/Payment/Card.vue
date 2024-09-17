<template>
  <div class="card-payment">
    <payment-error v-if="error" />
    <template v-else>
      <form>
        <div class="form-group">
          <div class="lonec-medu">
            <input type="text" name="name" placeholder="Your full name please" v-model="honeyPotName" />
            <input type="text" name="address" placeholder="Your address please" v-model="honeyPotAddress" />
            <input type="text" name="post" placeholder="Your postal code and office name please"
              v-model="honeyPotPost" />
          </div>
          <div id="cc-number" :class="[
              'form-control',
              'form-control-lg',
              { focus: numberFocused },
            ]" />
        </div>
        <div class="form-group">
          <div id="cc-expirationDate" :class="[
              'form-control',
              'form-control-lg',
              { focus: expirationDateFocused },
            ]" />
        </div>
        <div class="form-group">
          <div id="cc-cvv" :class="['form-control', 'form-control-lg', { focus: cvvFocused }]" />
        </div>
      </form>
      <div class="card-info">
        {{ $t('payment.cardNote') }}
        <br />
        <img src="https://s3.amazonaws.com/braintree-badges/braintree-badge-light.png" width="164" height="44"
          border="0" />
      </div>
    </template>
  </div>
</template>

<script>
import PaymentError from './Error.vue';
import braintree from 'braintree-web';

export default {
  components: {
    PaymentError,
  },
  props: {
    token: {
      type: String,
      required: true,
    },
    amount: {
      type: Number,
      required: true,
    },
    email: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      hostedFieldsInstance: null,
      threeDSecureInstance: null,
      error: null,
      numberFocused: false,
      expirationDateFocused: false,
      cvvFocused: false,
      formValid: false,
      paymentInProgress: false,
      honeyPotName: '',
      honeyPotAddress: '',
      honeyPotPost: '',
    };
  },
  async mounted() {
    if (braintree) {
      try {
        const clientInstance = await braintree.client.create({
          authorization: this.token,
        });
        const placeholderStyle = {
          // 'font-style': 'italic',
          // 'font-weight': '300',
          color: '#444',
          // 'text-decoration': 'underline',
        };
        const options = {
          client: clientInstance,
          styles: {
            input: {
              'font-size': '19.2px',
              'font-family': 'monospace',
            },
            'input.invalid': {
              color: '#dd786b',
            },
            // placeholder styles need to be individually adjusted
            '::-webkit-input-placeholder': placeholderStyle,
            '::-ms-input-placeholder': placeholderStyle,
            '::placeholder': placeholderStyle,
          },
          fields: {
            number: {
              selector: '#cc-number',
              placeholder: "Številka kartice",
            },
            expirationDate: {
              selector: '#cc-expirationDate',
              placeholder: "Rok veljavnosti",
            },
            cvv: {
              selector: '#cc-cvv',
              placeholder: "CVV",
            },
          },
        };
        this.hostedFieldsInstance = await braintree.hostedFields.create(
          options,
        );
        this.threeDSecureInstance = await braintree.threeDSecure.create({
          client: clientInstance,
          version: 2,
        });

        this.hostedFieldsInstance.on('focus', (event) => {
          this[`${event.emittedBy}Focused`] = true;
        });
        this.hostedFieldsInstance.on('blur', (event) => {
          this[`${event.emittedBy}Focused`] = false;
        });
        this.hostedFieldsInstance.on('validityChange', (event) => {
          const formValid = Object.keys(event.fields).every((key) => {
            return event.fields[key].isValid;
          });
          this.formValid = formValid;
          this.$emit('validity-change', formValid);
        });
        this.hostedFieldsInstance.on('inputSubmitRequest', () => {
          this.payWithCreditCard();
        });

        this.$emit('ready', { pay: this.payWithCreditCard });
      } catch (error) {
        // eslint-disable-next-line no-console
        // console.error(error);
        this.error = error;
        this.$emit('error', { error });
      }
    }
  },
  methods: {
    payWithCreditCard() {
      if (
        this.honeyPotName !== '' ||
        this.honeyPotAddress !== '' ||
        this.honeyPotPost !== ''
      ) {
        this.error = 'Preveč medu.';
        this.$emit('error', 'Preveč medu.');
      } else if (this.hostedFieldsInstance && !this.paymentInProgress) {
        this.paymentInProgress = true;
        this.$emit('payment-start');
        this.error = null;
        this.hostedFieldsInstance
          .tokenize({
            vault: true,
          })
          .then((payload) => {
            return this.threeDSecureInstance.verifyCard({
              onLookupComplete: (data, next) => next(),
              amount: this.amount,
              nonce: payload.nonce,
              bin: payload.details.bin,
              email: this.email,
              challengeRequested: true,
            });
          })
          .then((payload) => {
            if (!payload.liabilityShifted) {
              console.log('Liability did not shift', payload);
              this.error = 'Avtentikacija plačila ni uspela.';
              this.$emit('error', { message: this.error });
            } else {
              this.$emit('success', { nonce: payload.nonce });
            }
          })
          .catch((error) => {
            // eslint-disable-next-line no-console
            // console.error(error);
            this.error = error.message;
            this.$emit('error', { error });
          });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.card-payment {
  width: 100%;
  max-width: 350px;
  margin: 0 auto;

  .focus {
    border: 1px solid black;
    box-shadow: 0 0 0 0.2rem rgba(black, 0.25);
  }

  .loader-container {
    display: flex;
    justify-content: center;
    margin: 3rem 0;

    &.load-container--small {
      margin: 1rem 0;
    }
  }

  .card-info {
    font-weight: 300;
    font-size: 1rem;
    text-align: center;

    img {
      margin-top: 0.5rem;
    }
  }
}

</style>
