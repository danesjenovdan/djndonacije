<template>
  <div class="upn-payment">
    <form>
      <div class="qr-code-container">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div v-if="ready && qrCode" class="qr-code" v-html="qrCode"></div>
      </div>
      <div class="form-group">
        <label>{{ $t("payment.depositSlipNote") }}</label>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: "UpnPayment",
  props: {
    amount: {
      type: Number,
      required: true,
    },
    qrCode: {
      type: String,
      default: null,
    },
  },
  emits: ["ready", "success"],
  data() {
    return {
      ready: false,
    };
  },
  watch: {
    qrCode(newVal) {
      if (newVal) {
        this.setReady();
      }
    },
  },
  mounted() {
    if (this.qrCode) {
      this.setReady();
    }
  },
  methods: {
    setReady() {
      if (!this.ready) {
        this.ready = true;
        this.$emit("ready", { pay: this.sendUPN });
      }
    },
    sendUPN() {
      this.$emit("success");
    },
  },
};
</script>

<style lang="scss" scoped>
.upn-payment {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 360px;
  margin: 0 auto;

  label {
    font-size: 1rem;
    font-weight: 300;
    text-align: center;
    display: block;
    padding-top: 1rem;
  }

  .qr-code-container {
    .qr-code {
      display: block;
      width: 170px;
      height: auto;
      margin-inline: auto;

      @media (min-width: 360px) {
        width: 255px;
        height: 255px;
      }

      :deep(svg) {
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
