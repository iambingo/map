package com.map;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.map.mapper")
public class MapApplication {

    public static void main(String[] args) {
        SpringApplication.run(MapApplication.class, args);
    }
}
