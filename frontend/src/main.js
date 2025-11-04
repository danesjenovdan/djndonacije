import axios from "axios";
import { createApp } from "vue";
import VueAxios from "vue-axios";
import App from "./App.vue";
import i18n from "./i18n.js";
import router from "./router/index.js";
import store from "./store/index.js";

import "./assets/main.scss";

const app = createApp(App);

app.use(router);
app.use(store);
app.use(i18n);
app.use(VueAxios, axios);

app.mount("#app");
