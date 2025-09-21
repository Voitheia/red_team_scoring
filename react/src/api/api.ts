
// TODO: This really should be using the JWT or an authenticated API of some kind.

export interface LoginResponse {
  token: string;
  userid: string;
  username: string
}

export interface DeployIOCsResponse {
  status: string;
  message: string;
  results: any; 
}

export interface RunChecksResponse {
  status: string;
  message: string;
  details: {
    total_checks: number;
    last_check: string | null; 
  };
}

export interface CompetitionStatusResponse {
  status: string;
  message: string;
  details: any;  // Adjust as needed from get_status_info()
}

export interface SystemStatus {
  // Define according to what orch.get_status() returns
  [key: string]: any;
}

export interface ResetDataResponse {
  status: string;
  message: string;
}

const API_BASE = "http://localhost:3000/admin";

export async function deployIOCs(): Promise<DeployIOCsResponse> {
  const response = await fetch(`${API_BASE}/deploy_iocs`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Deploy IOCs failed: ${errorText}`);
  }
  return response.json();
}

export async function runChecks(): Promise<RunChecksResponse> {
  const response = await fetch(`${API_BASE}/run_checks`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Run checks failed: ${errorText}`);
  }
  return response.json();
}

export async function startCompetition(): Promise<CompetitionStatusResponse> {
  const response = await fetch(`${API_BASE}/start_comp`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Start competition failed: ${errorText}`);
  }
  return response.json();
}

export async function stopCompetition(): Promise<CompetitionStatusResponse> {
  const response = await fetch(`${API_BASE}/stop_comp`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Stop competition failed: ${errorText}`);
  }
  return response.json();
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_BASE}/status`);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Get status failed: ${errorText}`);
  }
  return response.json();
}

export async function resetCompetitionData(): Promise<ResetDataResponse> {
  const response = await fetch(`${API_BASE}/reset_data`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Reset data failed: ${errorText}`);
  }
  return response.json();
}


export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch("http://localhost:3000/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`);
  }
  return response.json();

  //let response: LoginResponse = {token: "ABCDEFG123",userid:  "58", username: "redteam"};
  //return response;
}