<template>
  <div class="checkout">
    <div class="nothing">
      <div>
        <h1>404</h1>
        <p>
          Tukaj ni ničesar. Pojdi na
          <a href="https://danesjenovdan.si/">danesjenovdan.si</a>.
        </p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins/breakpoints";

.checkout {
  .nothing {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 25%;
    text-align: center;
  }

  h1 {
    font-size: 40px;
    font-weight: 700;
    color: #333333;

    @include media-breakpoint-up(md) {
      font-size: 60px;
    }
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
