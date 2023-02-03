<template>
  <div class="upn-payment">
    <form>
      <img id="poloznica-img" src="../../assets/poloznica.png" />
      <div class="form-group">
        <label>Položnico ti bomo poslali po e-pošti.</label>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  props: {
  },
  data() {
    return {
    };
  },
  mounted() {
    this.$emit("ready", { pay: this.sendUPN });
  },
  methods: {
    sendUPN() {
      this.$emit("success");
    },
  },
};
</script>

<style lang="scss" scoped>
.upn-payment {
  max-width: 350px;
  margin: 0 auto;

  label {
    font-size: 1.25rem;
    font-weight: 300;
    text-align: center;
    display: block;
    padding-top: 10px;
    padding-bottom: 30px;
  }

  #poloznica-img {
    width: 100px;
    height: auto;
    margin: auto;
    display: block;
    margin-bottom: 10px;
    padding-top: 40px;
  }
}
</style>
