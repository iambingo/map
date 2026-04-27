package com.map.common;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Getter;

import java.io.Serial;
import java.io.Serializable;

/**
 * 统一 API 响应体
 */
@Getter
@JsonInclude(JsonInclude.Include.NON_NULL)
public class Result<T> implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    private final int code;
    private final String message;
    private final T data;
    private final long timestamp;

    private Result(int code, String message, T data) {
        this.code = code;
        this.message = message;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "success", data);
    }

    public static <T> Result<T> success() {
        return new Result<>(200, "success", null);
    }

    public static <T> Result<T> error(int code, String message) {
        return new Result<>(code, message, null);
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null);
    }

    public static <T> Result<T> badRequest(String message) {
        return new Result<>(40000, message, null);
    }

    public static <T> Result<T> unauthorized(String message) {
        return new Result<>(40100, message, null);
    }

    public static <T> Result<T> forbidden(String message) {
        return new Result<>(40300, message, null);
    }

    public static <T> Result<T> notFound(String message) {
        return new Result<>(40400, message, null);
    }
}
