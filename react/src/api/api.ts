export interface LoginResponse {
  token: string;
  userid: string;
  username: string
  admin: boolean,
  is_blue_team: boolean,
  blueteam_num: number
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

export interface UserSummary {
  user_id: number;
  username: string;
  is_admin: boolean;
  is_blue_team: boolean;
  blueteam_num: number | null;
}

export interface GetUsersResponse {
  status: string;
  users: UserSummary[];
}

const API_BASE = "http://localhost:3000";


export async function getUsers(): Promise<GetUsersResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/get_users`, {
    method: "GET",
    headers: { Authorization: `Bearer ${storedToken}` },
  });
  if (!response.ok) {
    throw new Error(`getUsers failed: ${response.statusText}`);
  }
  return response.json();
}

export async function removeUser(body: { user_id: number }): Promise<any> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/remove_user`, {
    method: "DELETE",
    headers: { 
      Authorization: `Bearer ${storedToken}`,
      "Content-Type": "application/json" 
      },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`removeUser failed: ${text}`);
  }
  return response.json();
}

export async function changePassword(body: {
  user_id: number;
  password: string;
}): Promise<any> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/change_password`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${storedToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Change password failed: ${text}`);
  }

  return response.json();
}

export async function addUser(body: {
  user_id: number;
  username: string;
  password: string;
  is_admin: boolean;
  is_blue_team: boolean;
  blueteam_num: number | null;
}): Promise<any> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/add_user`, {
    method: "POST",
    headers: { 
    Authorization: `Bearer ${storedToken}`,
    "Content-Type": "application/json" 
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`addUser failed: ${text}`);
  }
  return response.json();
}


export async function deployIOCs(): Promise<DeployIOCsResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/deploy_iocs`,
  {
    headers: { Authorization: `Bearer ${storedToken}` },
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Deploy IOCs failed: ${errorText}`);
  }
  return response.json();
}

export async function runChecks(): Promise<RunChecksResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/run_checks`, {
    headers: { Authorization: `Bearer ${storedToken}` },
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Run checks failed: ${errorText}`);
  }
  return response.json();
}

export async function startCompetition(): Promise<CompetitionStatusResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/start_comp`, {
    headers: { Authorization: `Bearer ${storedToken}` },
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Start competition failed: ${errorText}`);
  }
  return response.json();
}

export async function stopCompetition(): Promise<CompetitionStatusResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/stop_comp`, {
    headers: { Authorization: `Bearer ${storedToken}` },
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Stop competition failed: ${errorText}`);
  }
  return response.json();
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/status`, {
    
    headers: { Authorization: `Bearer ${storedToken}` }   
});
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Get status failed: ${errorText}`);
  }
  return response.json();
}

export async function resetCompetitionData(): Promise<ResetDataResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/admin/reset_data`, {
    headers: { Authorization: `Bearer ${storedToken}` },
    method: "POST",
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Reset data failed: ${errorText}`);
  }
  return response.json();
}


export async function login(username: string, password: string): Promise<LoginResponse> {
  const storedToken = localStorage.getItem("authToken");
  const response = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${storedToken}`,
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