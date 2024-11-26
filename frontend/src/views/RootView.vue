<template>
  <div class="checkout">
    <div class="nothing">
      <p>
        Tukaj ni ničesar. Pojdi na
        <a href="https://danesjenovdan.si/">danesjenovdan.si</a>.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {};
  },
};
</script>

<style lang="scss" scoped>
@import "@/assets/main.scss";

.checkout {
  .nothing {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 25%;
    text-align: center;
  }

  p {
    font-size: 20px;
    color: #333333;
    font-weight: 200;
    width: 100%;
    max-width: 872px;
    margin-top: 20px;
    margin-bottom: 20px;
    padding-left: 30px;
    padding-right: 30px;

    @include media-breakpoint-up(md) {
      font-size: 30px;
      padding: 0;
    }
  }
}
</style>
