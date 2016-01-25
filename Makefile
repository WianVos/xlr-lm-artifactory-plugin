all: build_jar release_github


build_jar:
	./gradlew build 

release_github:
	./gradlew githubRelease
