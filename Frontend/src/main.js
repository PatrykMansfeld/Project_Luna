// Punkt wejścia aplikacji Vue
import { createApp } from 'vue'
import './style.css' // Globalne style (zmienne CSS, reset, dark mode)
import App from './App.vue' // Główny komponent aplikacji

// Tworzy instancję Vue i montuje ją do elementu <div id="app"> w index.html
createApp(App).mount('#app')
