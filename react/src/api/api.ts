export interface LoginResponse {
  token: string;
  userid: string;
  username: string
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  /*const response = await fetch("http://localhost:5000/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.statusText}`);
  }
  return response.json();*/

  let response: LoginResponse = {token: "ABCDEFG123",userid:  "58", username: "redteam"};
  return response;
}