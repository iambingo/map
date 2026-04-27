package com.map.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@TableName("sys_user")
public class User extends BaseEntity {

    private String username;
    private String password;
    private String nickname;
    private String email;
    private String role;      // SUPER_ADMIN | FUND_MANAGER | RISK_OFFICER | ANALYST | VIEWER
    private String avatar;
    private Boolean enabled;
    private String lastLoginAt;
}
