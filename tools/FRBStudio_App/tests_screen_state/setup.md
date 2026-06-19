https://nodejs.org/en/download

node-v24.17.0-x64.msi

node -v
npm -v

cd F:\FRB\tools\FRBStudio_App
mkdir tests_screen_state
cd tests_screen_state
npm init playwright@latest

npx playwright test

npx playwright test --headed


npx playwright test --ui
