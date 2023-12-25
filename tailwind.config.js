// Resolve path to directory containing manage.py file.
// This is the root of the project.
// Then assumed layout of <main-app>/static/css/tailwind.config.js, so up 3 levels.
// Adjust for your needs.
const path = require('path');
const projectRoot = path.resolve(__dirname, '');

const {spawnSync} = require('child_process');

// Function to execute the Django management command and capture its output
const getTemplateFiles = () => {
    const command = 'python'; // Requires virtualenv to be activated.
    const args = ['manage.py', 'list_templates']; // Requires cwd to be set.
    const options = {cwd: projectRoot};
    const result = spawnSync(command, args, options);

    if (result.error) {
        throw result.error;
    }

    if (result.status !== 0) {
        console.log(result.stdout.toString(), result.stderr.toString());
        throw new Error(`Django management command exited with code ${result.status}`);
    }

    const templateFiles = result.stdout.toString()
        .split('\n')
        .map((file) => file.trim())
        .filter(function (e) {
            return e
        });  // Remove empty strings, including last empty line.
    return templateFiles;
};

module.exports = {
    // Allow configuring some folders manually, and then concatenate with the
    // output of the Django management command.
    content: [].concat(getTemplateFiles()),
    safelist: [
        "bg-yellow-600",
        "bg-blue-300",
        "bg-green-400",
        "bg-gray-400",
        "bg-red-50",
        "bg-lime-800",
        "aria-disabled",
        "aria-readonly",
        "pattern-zigzag",
        "pattern-red-500",
        "pattern-rhombus",
        "pattern-yellow-500",
    ],
    variants: {
        extend: {
            opacity: ['disabled'],
        }
    },
    theme: {
        container: {
            center: true,
        },
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('tailwindcss-bg-patterns'),
    ],
}
