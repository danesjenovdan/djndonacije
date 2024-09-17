import { createI18n } from "vue-i18n"; 
import sl from "./locales/sl.json";
import en from "./locales/en.json";

export default createI18n({
  locale: "sl",
  messages: {
    sl,
    en,
  },
});