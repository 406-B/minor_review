/**
 * 单元测试：TopBar 组件
 * 测试顶部导航栏组件的渲染和导航功能
 */

import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import TopBar from '../TopBar.vue';

// Mock router
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/canteen', name: 'canteen' },
    { path: '/community', name: 'community' },
    { path: '/profile', name: 'profile' },
  ],
});

describe('TopBar Component', () => {
  it('should render app title correctly', () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const title = wrapper.find('.app-title');
    expect(title.text()).toBe('小众点评');
    expect(title.exists()).toBe(true);
  });

  it('should render navigation items', () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const navItems = wrapper.findAll('.nav-item');
    expect(navItems).toHaveLength(2);
    expect(navItems[0].text()).toBe('食堂浏览');
    expect(navItems[1].text()).toBe('美食论坛');
  });

  it('should render user profile text', () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const profileText = wrapper.find('.user-profile-text');
    expect(profileText.text()).toBe('个人主页');
    expect(profileText.exists()).toBe(true);
  });

  it('should navigate to canteen page when clicking 食堂浏览', async () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const canteenNav = wrapper.find('.nav-item');
    await canteenNav.trigger('click');

    expect(router.currentRoute.value.path).toBe('/canteen');
  });

  it('should navigate to community page when clicking 美食论坛', async () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const communityNav = wrapper.findAll('.nav-item')[1];
    await communityNav.trigger('click');

    expect(router.currentRoute.value.path).toBe('/community');
  });

  it('should navigate to profile page when clicking 个人主页', async () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const profileNav = wrapper.find('.user-profile-text');
    await profileNav.trigger('click');

    expect(router.currentRoute.value.path).toBe('/profile');
  });

  it('should have correct CSS classes and styling', () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const topBar = wrapper.find('.top-bar');
    expect(topBar.classes()).toContain('top-bar');

    // Check if scoped styles are applied
    expect(topBar.attributes('class')).toContain('top-bar');
  });

  it('should be sticky positioned', () => {
    const wrapper = mount(TopBar, {
      global: {
        plugins: [router],
      },
    });

    const topBar = wrapper.find('.top-bar');
    expect(topBar.element.style.position).toBe('sticky');
  });
});
