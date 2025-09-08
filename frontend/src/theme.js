// theme.js
import { extendTheme } from "@chakra-ui/react";

const theme = extendTheme({
  colors: {
    brand: {
      900: "#8B0000", // Dark red for buttons
      800: "#0A0B2E", // Navy for sidebar
    },
    purple: {
      500: "#5b47fb",
      600: "#4935e8",
    },
    navy: {
      800: "#0a0b2e",
      900: "#070818",
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: "normal",
      },
    },
    Table: {
      variants: {
        simple: {
          th: {
            borderBottom: "1px",
            borderColor: "gray.200",
            textTransform: "none",
            fontSize: "sm",
            fontWeight: "medium",
          },
          td: {
            borderBottom: "1px",
            borderColor: "gray.200",
            fontSize: "sm",
          },
        },
      },
    },
  },
});

export default theme;
