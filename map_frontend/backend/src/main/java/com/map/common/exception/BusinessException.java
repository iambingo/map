package com.map.common.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {

    private final int code;

    public BusinessException(String message) {
        super(message);
        this.code = 50000;
    }

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    public static BusinessException notFound(String resource) {
        return new BusinessException(40400, resource + " 不存在");
    }

    public static BusinessException forbidden(String msg) {
        return new BusinessException(40300, msg);
    }
}
