import { createI18n } from "vue-i18n";
import en from "./locales/en.json";
import sl from "./locales/sl.json";

export default createI18n({
  locale: "sl",
  messages: {
    sl,
    en,
  },
});
