
export async function loginUser(username, password) {
    const response = await fetch("https://localhost:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });
  
    if (!response.ok) {
      throw new Error("Login failed");
    }
  
    return await response.json();
  }