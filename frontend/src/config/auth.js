export const AUTH_CONFIG = {
  motor: {
    authorizedEmails: ["sakay@nicl.mu", "mhosenbocus@nicl.mu", "vikas.khanna@zwennpay.com"],
    superPassword: "NICLMOTOR@2025",
    teamName: "Motor Insurance Team",
    theme: "motor-theme"
  },
  health: {
    authorizedEmails: ["mjugun@nicl.mu", "sheeralall@nicl.mu", "vikas.khanna@zwennpay.com"],
    superPassword: "NICLHEALTH@2025", 
    teamName: "Health Insurance Team",
    theme: "health-theme"
  }
};

export const detectTeam = (email) => {
  if (AUTH_CONFIG.motor.authorizedEmails.includes(email)) {
    return 'motor';
  }
  if (AUTH_CONFIG.health.authorizedEmails.includes(email)) {
    return 'health';
  }
  return null;
};

export const getTeamConfig = (team) => {
  return AUTH_CONFIG[team] || null;
};