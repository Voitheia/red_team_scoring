export interface Score {
    team_id: number
    team_name: string,
    score: number
}

export interface LoginRequest {
    username: string
    password: string
}

export interface LoginResponse {
    message: string
}

export interface RegisterRequest {
    username: string
    password: string
    admin: boolean
}

export interface RegisterResponse {
    username: string
    password: string
    admin: boolean
}
