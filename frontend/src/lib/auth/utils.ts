import Cookies from "js-cookie";

const TOKEN_KEY = "access_token";

export const tokenUtils = {
  setToken: (token: string) => {
    Cookies.set(TOKEN_KEY, token, { expires: 7 }); // 7 days
  },

  getToken: (): string | undefined => {
    return Cookies.get(TOKEN_KEY);
  },

  removeToken: () => {
    Cookies.remove(TOKEN_KEY);
  },
};


