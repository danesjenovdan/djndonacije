import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // root
    {
      path: "/",
      name: "root",
      component: () => import("../views/RootView.vue"),
    },
    // urejanje donacij
    {
      path: "/urejanje-donacij",
      name: "manageDonations",
      component: () => import("../views/ManageDonationsView.vue"),
      meta: {
        title: "Urejanje donacij",
      },
    },
    // donacije posamezne kampanje
    {
      path: "/:campaignSlug/doniraj",
      component: () => import("../views/DonateView.vue"),
      name: "donate",
      children: [
        {
          path: "",
          name: "selectAmount",
          component: () => import("../views/SelectAmountView.vue"),
        },
        // {
        //   path: "info",
        //   name: "info",
        //   component: () => import("../views/InfoView.vue"),
        // },
        // {
        //   path: "placilo",
        //   name: "payment",
        //   component: () => import("../views/PaymentView.vue"),
        // },
        {
          path: "placilo",
          name: "payment",
          component: () => import("../views/PaymentNewView.vue"),
        },
      ],
    },
    {
      path: "/:campaignSlug/doniraj/hvala",
      name: "thankYou",
      component: () => import("../views/ThankYouView.vue"),
      meta: {
        title: "Hvala!",
      },
    },
    {
      path: "/:campaignSlug/doniraj/napaka",
      name: "paymentError",
      component: () => import("../views/PaymentErrorView.vue"),
      meta: {
        title: "Napaka!",
      },
    },
    // naročnine posamezne kampanje
    {
      path: "/:campaignSlug/urejanje-narocnine",
      name: "manageNewsletter",
      component: () => import("../views/ManageNewsletterView.vue"),
      meta: {
        title: "Urejanje naročnine",
      },
    },
    // 404 (last, catch-all route)
    {
      path: "/:notFound(.*)",
      name: "notFound",
      component: () => import("../views/NotFoundView.vue"),
    },
  ],
});

router.beforeEach((to, from, next) => {
  document.title = to.meta?.title ?? "Danes je nov dan";
  next();
});

export default router;
