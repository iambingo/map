package com.map.controller;

import com.map.common.Result;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    @PostMapping("/login")
    public Result<Void> login() {
        // TODO: 实现 JWT 登录逻辑
        return Result.error("待实现");
    }

    @PostMapping("/logout")
    public Result<Void> logout() {
        // TODO: 实现登出（加入黑名单）
        return Result.success();
    }

    @PostMapping("/refresh")
    public Result<Void> refresh() {
        // TODO: 实现 Refresh Token
        return Result.error("待实现");
    }

    @GetMapping("/me")
    public Result<Void> me() {
        // TODO: 返回当前用户信息
        return Result.error("待实现");
    }
}
