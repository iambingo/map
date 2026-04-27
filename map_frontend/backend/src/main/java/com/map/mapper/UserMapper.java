package com.map.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.map.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
