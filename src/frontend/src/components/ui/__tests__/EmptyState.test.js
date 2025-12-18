/**
 * 单元测试：EmptyState 组件
 * 测试空状态组件的渲染和属性
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import EmptyState from '../EmptyState.vue';

describe('EmptyState Component', () => {
  it('should render default text when no text prop provided', () => {
    const wrapper = mount(EmptyState);

    const textElement = wrapper.find('p');
    expect(textElement.text()).toBe('暂无数据');
  });

  it('should render custom text when text prop is provided', () => {
    const customText = '没有找到相关内容';
    const wrapper = mount(EmptyState, {
      props: {
        text: customText,
      },
    });

    const textElement = wrapper.find('p');
    expect(textElement.text()).toBe(customText);
  });

  it('should not render icon when icon prop is not provided', () => {
    const wrapper = mount(EmptyState);

    const imgElement = wrapper.find('img');
    expect(imgElement.exists()).toBe(false);
  });

  it('should render icon when icon prop is provided', () => {
    const iconUrl = '/images/empty-icon.svg';
    const wrapper = mount(EmptyState, {
      props: {
        icon: iconUrl,
      },
    });

    const imgElement = wrapper.find('img');
    expect(imgElement.exists()).toBe(true);
    expect(imgElement.attributes('src')).toBe(iconUrl);
  });

  it('should render slot content', () => {
    const wrapper = mount(EmptyState, {
      slots: {
        default: '<button>刷新页面</button>',
      },
    });

    const button = wrapper.find('button');
    expect(button.exists()).toBe(true);
    expect(button.text()).toBe('刷新页面');
  });

  it('should have correct CSS classes', () => {
    const wrapper = mount(EmptyState);

    const container = wrapper.find('.ui-empty');
    expect(container.exists()).toBe(true);
    expect(container.classes()).toContain('ui-empty');
  });

  it('should render all elements in correct order', () => {
    const wrapper = mount(EmptyState, {
      props: {
        text: '测试文本',
        icon: '/test-icon.svg',
      },
      slots: {
        default: '<div>自定义内容</div>',
      },
    });

    const container = wrapper.find('.ui-empty');
    const elements = container.element.children;

    expect(elements[0].tagName).toBe('IMG');
    expect(elements[1].tagName).toBe('P');
    expect(elements[2].tagName).toBe('DIV');
  });
});
