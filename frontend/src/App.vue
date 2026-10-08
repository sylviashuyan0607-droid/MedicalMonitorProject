<template>
  <router-view :key="$route.fullPath" />
</template>

<style>
/* 让页面铺满全屏 */
body, html, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: #001529; /* 设置你想要的深色背景 */
}
</style>