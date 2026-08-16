# PHASE 7 — FRONTEND

## 1. Overview

The LightX-IDS frontend provides the user-facing dashboard for monitoring the Industrial IoT environment, viewing sensor information, monitoring attacks, interacting with IDS predictions, analyzing datasets, viewing system logs, and managing settings.

The frontend is implemented as a React application using Vite.

## 2. Frontend Technology Stack

- React
- Vite
- Tailwind CSS
- React Router
- Axios
- React Icons
- Chart.js / Recharts

## 3. Frontend Structure

The frontend is organized into reusable components, pages, routing, hooks, and supporting assets.

Major pages include:

- Dashboard
- Sensors
- Attack Monitoring
- IDS Prediction
- Dataset Analytics
- System Logs
- Settings
- Login
- Not Found

## 4. Application Routing

The frontend uses React Router for navigation between application pages.

Configured routes include:

| Route | Page |
|---|---|
| `/` | Dashboard |
| `/sensors` | Sensors |
| `/attacks` | Attack Monitoring |
| `/prediction` | IDS Prediction |
| `/dataset` | Dataset Analytics |
| `/logs` | System Logs |
| `/settings` | Settings |
| `/login` | Login |

A Not Found page is also used for invalid routes.

## 5. Dashboard

The Dashboard provides an overview of the Industrial IoT environment.

Dashboard components include:

- Temperature Chart
- Pressure Chart
- Stat Cards

The dashboard is intended to provide a centralized view of system and sensor information.

## 6. Sensors

The Sensors page provides the frontend interface for viewing sensor-related information from the Industrial IoT environment.

The application is designed to display sensor data received from the backend.

## 7. Attack Monitoring

The Attack Monitoring page provides an interface for monitoring cyberattack activity in the simulated industrial environment.

The backend attack framework includes:

- DoS Attack
- Replay Attack
- Injection Attack
- Spoofing Attack

The frontend provides the corresponding monitoring interface for attack-related information.

## 8. IDS Prediction

The IDS Prediction page provides the interface for interacting with intrusion detection predictions.

This page is intended to connect the frontend with the IDS prediction functionality provided by the backend.

## 9. Dataset Analytics

The Dataset Analytics page provides the frontend interface for viewing dataset-related information and analytics.

The project supports generated datasets as well as processed external datasets.

## 10. System Logs

The System Logs page provides an interface for viewing system-related logging information.

This allows system activity to be presented in a centralized frontend view.

## 11. Settings

The Settings page provides the interface for frontend/system configuration options.

## 12. Login

The Login page provides the authentication interface for accessing the application.

Authentication-related frontend functionality is handled through the application's authentication hook and routing structure.

## 13. API Configuration

The frontend is configured to communicate with the backend through an environment variable:

`VITE_API_URL`

The configured development backend URL used during development was:

`http://localhost:8000/api`

This allows the frontend API endpoint to be changed without modifying application source code.

## 14. Build and Deployment

The frontend is built using Vite.

The production build was successfully generated using:

`npm run build`

The generated production files are placed in the `dist/` directory.

The build generated the following main assets:

- `dist/index.html`
- CSS bundle
- JavaScript bundle

Vite also reported a warning about a JavaScript chunk exceeding the recommended 500 kB size after minification.

## 15. Current Implementation Status

The frontend pages and routing structure have been implemented and are working.

The frontend currently provides the user interface required for:

- Industrial monitoring
- Sensor visualization
- Attack monitoring
- IDS prediction
- Dataset analytics
- System logs
- Settings
- Authentication

Further backend integration and real-time functionality can be connected as the corresponding backend APIs and machine-learning components are completed.