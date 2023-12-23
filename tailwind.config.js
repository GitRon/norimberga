const Path = require("path");
const pySitePackages = process.env.pySitePackages || "";

/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'media',
    content: [
        "./apps/**/templates/**/*.html",
        "./static/**/*.js",
        Path.join(pySitePackages, "./crispy_tailwind/**/*.html"),
        Path.join(pySitePackages, "./crispy_tailwind/**/*.py"),
        Path.join(pySitePackages, "./crispy_tailwind/**/*.js"),
    ],
    safelist: [
        "bg-yellow-600",
        "bg-blue-300",
        "bg-green-400",
        "bg-gray-400",
        "bg-red-50",
    ],
    theme: {
        container: {
            center: true,
        },
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
