// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Vuetify
import { createVuetify } from 'vuetify'


const FavaTheme = {
  dark: true,
  colors: {
    background: '#2E282A', 
    "background-light": '#14281D', 
    primary: "#45B69C",
    secondary: '#170A1C',
    "secondary-light": '#453F78',
    bright: "#FFEFD3",
    error: '#a62639',
    "error-light": "#A24936",
    info: '#001B2E',
    "info-light": '#294C60',
    success: '#4CAF50',
    warning: '#EA8C55',
    "warning-light": "#EDB88B",
  }
}

export default createVuetify({
  theme: {
    defaultTheme: 'FavaTheme',
    themes: {
      FavaTheme,
    }
  }
})