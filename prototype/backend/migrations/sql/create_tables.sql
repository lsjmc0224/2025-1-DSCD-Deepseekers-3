-- 테이블 생성 SQL


CREATE TABLE collection_jobs (
	id VARCHAR(50) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	parameters JSON, 
	progress FLOAT NOT NULL, 
	message TEXT, 
	result JSON, 
	started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	completed_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE youtube_videos (
	youtube_id VARCHAR(20) NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	published_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	duration VARCHAR(20), 
	channel_id VARCHAR(50) NOT NULL, 
	channel_title VARCHAR(255) NOT NULL, 
	view_count INTEGER NOT NULL, 
	like_count INTEGER NOT NULL, 
	comment_count INTEGER NOT NULL, 
	thumbnail_url VARCHAR(255), 
	tags JSON, 
	category_id VARCHAR(10), 
	last_fetched_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE youtube_comments (
	video_id VARCHAR(36) NOT NULL, 
	comment_id VARCHAR(50) NOT NULL, 
	text TEXT NOT NULL, 
	author_name VARCHAR(100) NOT NULL, 
	author_channel_id VARCHAR(50), 
	author_profile_url VARCHAR(255), 
	like_count INTEGER NOT NULL, 
	published_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	is_reply BOOLEAN NOT NULL, 
	parent_id VARCHAR(50), 
	sentiment_score FLOAT, 
	sentiment_label VARCHAR(20), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(video_id) REFERENCES youtube_videos (id) ON DELETE CASCADE
)

;


CREATE TABLE youtube_sentiment_analysis (
	video_id VARCHAR(36) NOT NULL, 
	positive_count INTEGER NOT NULL, 
	negative_count INTEGER NOT NULL, 
	neutral_count INTEGER NOT NULL, 
	positive_percentage FLOAT NOT NULL, 
	negative_percentage FLOAT NOT NULL, 
	neutral_percentage FLOAT NOT NULL, 
	average_sentiment_score FLOAT NOT NULL, 
	positive_keywords JSON, 
	negative_keywords JSON, 
	analyzed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	analysis_version VARCHAR(20), 
	id VARCHAR(36) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (video_id), 
	FOREIGN KEY(video_id) REFERENCES youtube_videos (id) ON DELETE CASCADE
)

;