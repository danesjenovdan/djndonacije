import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import axios from "axios";
import VueAxios from "vue-axios";

import i18n from "./i18n"

import './assets/main.scss';

const app = createApp(App);

app.use(router);
app.use(store);
app.use(i18n);
app.use(VueAxios, axios);

app.mount("#app");
