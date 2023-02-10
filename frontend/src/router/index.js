import { createRouter, createWebHistory } from "vue-router";
import SelectAmountView from "../views/SelectAmountView.vue";
import InfoView from "../views/InfoView.vue";
import PaymentView from "../views/PaymentView.vue";
import ThankYouView from "../views/ThankYouView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/:donationSlug",
      name: "selectAmount",
      component: SelectAmountView,
      alias: '/:donationSlug/izberi'
    },
    {
      path: "/:donationSlug/info",
      name: "info",
      component: InfoView,
    },
    {
      path: "/:donationSlug/placilo",
      name: "payment",
      component: PaymentView,
    },
    {
      path: "/hvala",
      name: "thankYou",
      component: ThankYouView,
    },
  ],
});

export default router;
