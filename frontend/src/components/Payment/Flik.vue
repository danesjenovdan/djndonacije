<template>
  <div class="upn-payment">
    <form>
      <svg
        id="flik-logo"
        xmlns="http://www.w3.org/2000/svg"
        width="80"
        height="80"
        viewBox="0 0 80 80"
      >
        <circle r="40" cx="40" cy="40" fill="transparent"></circle>
        <path
          fill="#1D1D1D"
          fill-rule="evenodd"
          d="M45 30.5a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0zM57 48h2V29h-2v19zm11 0h-2.616L60 41.463 65.044 35h2.609l-5.189 6.448L68 48zm-19.49-1.82H53V48H42v-1.82h4.251v-9.36H42.4V35h6.11v11.18zm-15.001-.014H38V48H27v-1.834h4.251V30.834h-3.985V29h6.243v17.166zM20.765 29c.744 0 1.36.078 2.235.26v1.958c-.565-.079-1.26-.208-2.235-.208-1.954 0-2.649.678-2.649 2.662v1.278H23v1.8h-4.884v2.095H23v1.801h-4.884V48h-2.183v-7.354H12v-1.8h3.933V36.75H12v-1.8h3.933v-1.435c0-2.975 1.644-4.515 4.832-4.515zm19.234 49C19.046 78 2 60.954 2 40S19.046 2 40 2c20.953 0 38 17.046 38 38S60.953 78 40 78zM40 0C17.91 0 0 17.909 0 40c0 22.092 17.909 40 40 40s40-17.908 40-40C80 17.91 62.091 0 40 0z"
        ></path>
      </svg>
      <div class="form-group">
        <label>{{ $t("payment.flikNote") }}</label>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: "FlikPayment",
  emits: ["ready", "success"],
  mounted() {
    this.$emit("ready", { pay: this.sendFlikRequest });
  },
  methods: {
    sendFlikRequest() {
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

  #flik-logo {
    display: block;
    width: 80px;
    height: auto;
    margin-inline: auto;
    margin-block: 0.5rem;
  }
}
</style>
