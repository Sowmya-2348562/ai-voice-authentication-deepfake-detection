function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains("dark-mode") ? "dark" : "light";
    const newTheme = currentTheme === "light" ? "dark-mode" : "light-mode";
    body.classList.toggle("dark-mode");
    body.classList.toggle("light-mode");
    localStorage.setItem("theme", newTheme);
  }
  
  document.body.classList.add("show-loader");

  window.onload = () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      document.body.classList.remove("light-mode", "dark-mode");
      document.body.classList.add(savedTheme);
    }
  };
  