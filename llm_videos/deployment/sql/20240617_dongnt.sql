CREATE  TABLE users (
    user_id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    email varchar(150) COLLATE utf8mb4_unicode_ci,
    password varchar(250) NOT NULL,
    avatar varchar(250) DEFAULT NULL,
    source_register ENUM('manual', 'facebook', 'google') DEFAULT "manual",
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE  TABLE account_config (
    user_id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    target_language varchar(20) COLLATE utf8mb4_unicode_ci,
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE TABLE videos (
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    title varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
    description text COLLATE utf8mb4_unicode_ci,
    thumbnail_url varchar(250) COLLATE utf8mb4_unicode_ci,
    video_url varchar(250) COLLATE utf8mb4_unicode_ci,
    video_id varchar(200) COLLATE utf8mb4_unicode_ci,
    lang varchar(20) COLLATE utf8mb4_unicode_ci,
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE TABLE video_subtitles (
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    video_id bigint(20) COLLATE utf8mb4_unicode_ci NOT NULL,
    language varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
    content longtext COLLATE utf8mb4_unicode_ci NOT NULL,
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE TABLE authentication(
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id bigint(20) NOT NULL,
    device_id varchar(250) COLLATE utf8mb4_unicode_ci,
    access_token varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
    expired_at int(11) NOT NULL,
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;



CREATE TABLE chats (
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id bigint(20) NOT NULL,
    channel_id varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
    video_id bigint(20) NOT NULL,
    message text COLLATE utf8mb4_unicode_ci,
    type ENUM('system', 'human') DEFAULT "human",
    status ENUM('success', 'pending', 'error') DEFAULT "pending",
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE TABLE users_upload (
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id bigint(20) NOT NULL,
    video_id bigint(20) NOT NULL,
    status ENUM('success', 'pending', 'error') DEFAULT "pending",
    translate_processing_status ENUM('success', 'pending', 'error') DEFAULT "pending",
    vector_index_status ENUM('success', 'pending', 'error') DEFAULT "pending",
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;


CREATE TABLE background_jobs (
    id bigint(20) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id bigint(20) NOT NULL,
    video_id bigint(20) NOT NULL,
    job_id varchar(250) COLLATE utf8mb4_unicode_ci NOT NULL,
    status ENUM('success', 'pending', 'error') DEFAULT "pending",
    target_language varchar(20) COLLATE utf8mb4_unicode_ci,
    description varchar(250) COLLATE utf8mb4_unicode_ci,
    created_at int(11) NOT NULL,
    updated_at int(11) NOT NULL
) ENGINE=InnoDB COLLATE=utf8mb4_unicode_ci;
