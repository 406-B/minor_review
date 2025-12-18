/**
 * 单元测试：ImageUploader 组件
 * 测试图片上传组件的功能和交互
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import ImageUploader from '../ImageUploader.vue';

// Mock File API
global.File = class MockFile {
  constructor(bits, filename, options = {}) {
    this.bits = bits;
    this.name = filename;
    this.type = options.type || 'image/jpeg';
    this.size = bits.length;
  }
};

global.FileReader = class MockFileReader {
  constructor() {
    this.result = null;
    this.onload = null;
    this.onerror = null;
  }

  readAsDataURL(file) {
    // 模拟读取文件
    setTimeout(() => {
      this.result = `data:${file.type};base64,${btoa('mock image data')}`;
      if (this.onload) this.onload();
    }, 0);
  }
};

describe('ImageUploader Component', () => {
  let wrapper;
  let mockEmit;

  beforeEach(() => {
    mockEmit = vi.fn();
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: [],
        maxImages: 5,
      },
      attrs: {
        onUpdateModelValue: mockEmit,
      },
    });
  });

  it('should render with default props', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.image-uploader').exists()).toBe(true);
    expect(wrapper.find('.upload-box-empty').exists()).toBe(true);
    expect(wrapper.text()).toContain('添加图片');
    expect(wrapper.text()).toContain('最多5张');
  });

  it('should display existing images when modelValue is provided', async () => {
    const existingImages = ['image1.jpg', 'image2.jpg'];

    await wrapper.setProps({ modelValue: existingImages });

    expect(wrapper.find('.images-preview').exists()).toBe(true);
    expect(wrapper.findAll('.image-item')).toHaveLength(2);
    expect(wrapper.find('.upload-box').exists()).toBe(true);
  });

  it('should not show upload box when max images reached', async () => {
    const maxImages = ['img1.jpg', 'img2.jpg', 'img3.jpg'];

    await wrapper.setProps({
      modelValue: maxImages,
      maxImages: 3,
    });

    expect(wrapper.find('.upload-box').exists()).toBe(false);
  });

  it('should emit update:modelValue when image is removed', async () => {
    const existingImages = ['image1.jpg', 'image2.jpg'];

    await wrapper.setProps({ modelValue: existingImages });

    const removeButtons = wrapper.findAll('.remove-btn');
    expect(removeButtons).toHaveLength(2);

    // 点击删除第一张图片
    await removeButtons[0].trigger('click');

    expect(mockEmit).toHaveBeenCalledWith(['image2.jpg']);
  });

  it('should handle file selection', async () => {
    const fileInput = wrapper.find('input[type="file"]');
    expect(fileInput.exists()).toBe(true);
    expect(fileInput.attributes('multiple')).toBeDefined();
    expect(fileInput.attributes('accept')).toBe('image/*');
  });

  it('should validate file type', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    // 创建非图片文件
    const textFile = new File(['text content'], 'test.txt', { type: 'text/plain' });

    // Mock文件选择
    Object.defineProperty(fileInput.element, 'files', {
      value: [textFile],
      writable: false,
    });

    await fileInput.trigger('change');

    // 应该过滤掉非图片文件，不发出更新事件
    expect(mockEmit).not.toHaveBeenCalled();
  });

  it('should validate file size', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    // 创建超过大小限制的文件 (假设限制为5MB，这里创建6MB)
    const largeFile = new File([new ArrayBuffer(6 * 1024 * 1024)], 'large.jpg', {
      type: 'image/jpeg',
    });

    Object.defineProperty(fileInput.element, 'files', {
      value: [largeFile],
      writable: false,
    });

    await fileInput.trigger('change');

    // 应该过滤掉大文件
    expect(mockEmit).not.toHaveBeenCalled();
  });

  it('should handle multiple file selection', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    const files = [
      new File(['file1'], 'image1.jpg', { type: 'image/jpeg' }),
      new File(['file2'], 'image2.jpg', { type: 'image/jpeg' }),
      new File(['file3'], 'image3.jpg', { type: 'image/jpeg' }),
    ];

    Object.defineProperty(fileInput.element, 'files', {
      value: files,
      writable: false,
    });

    await fileInput.trigger('change');

    // 应该发出包含所有文件的更新事件
    expect(mockEmit).toHaveBeenCalled();
    const emittedValue = mockEmit.mock.calls[0][0];
    expect(emittedValue).toHaveLength(3);
  });

  it('should respect maxImages limit', async () => {
    await wrapper.setProps({ modelValue: ['img1.jpg'], maxImages: 2 });

    const fileInput = wrapper.find('input[type="file"]');
    const files = [
      new File(['file1'], 'image1.jpg', { type: 'image/jpeg' }),
      new File(['file2'], 'image2.jpg', { type: 'image/jpeg' }),
      new File(['file3'], 'image3.jpg', { type: 'image/jpeg' }), // 超过限制
    ];

    Object.defineProperty(fileInput.element, 'files', {
      value: files,
      writable: false,
    });

    await fileInput.trigger('change');

    // 应该只添加2张图片（1张已有 + 1张新加，达到限制）
    expect(mockEmit).toHaveBeenCalled();
    const emittedValue = mockEmit.mock.calls[0][0];
    expect(emittedValue).toHaveLength(2);
  });

  it('should show preview for uploaded images', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    const file = new File(['image data'], 'test.jpg', { type: 'image/jpeg' });

    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      writable: false,
    });

    await fileInput.trigger('change');

    // 等待文件读取完成
    await nextTick();

    expect(mockEmit).toHaveBeenCalled();
    const emittedValue = mockEmit.mock.calls[0][0];
    expect(emittedValue).toHaveLength(1);
    expect(emittedValue[0]).toContain('data:image/jpeg;base64,');
  });

  it('should handle FileReader errors', async () => {
    // Mock FileReader 错误
    const originalFileReader = global.FileReader;
    global.FileReader = class MockFileReader {
      constructor() {
        this.result = null;
        this.onload = null;
        this.onerror = null;
      }

      readAsDataURL(file) {
        setTimeout(() => {
          if (this.onerror) this.onerror(new Error('Read failed'));
        }, 0);
      }
    };

    const fileInput = wrapper.find('input[type="file"]');
    const file = new File(['data'], 'test.jpg', { type: 'image/jpeg' });

    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      writable: false,
    });

    await fileInput.trigger('change');

    // 恢复原始 FileReader
    global.FileReader = originalFileReader;

    // 应该不发出更新事件
    expect(mockEmit).not.toHaveBeenCalled();
  });

  it('should trigger file input when upload box is clicked', async () => {
    const uploadBox = wrapper.find('.upload-box-empty');
    const fileInput = wrapper.find('input[type="file"]');

    const clickSpy = vi.fn();
    fileInput.element.click = clickSpy;

    await uploadBox.trigger('click');

    expect(clickSpy).toHaveBeenCalled();
  });

  it('should update when modelValue changes externally', async () => {
    expect(wrapper.find('.upload-box-empty').exists()).toBe(true);

    await wrapper.setProps({ modelValue: ['external.jpg'] });

    expect(wrapper.find('.images-preview').exists()).toBe(true);
    expect(wrapper.find('.upload-box-empty').exists()).toBe(false);
  });

  it('should handle drag and drop events', async () => {
    const uploadBox = wrapper.find('.upload-box-empty');

    // 模拟拖拽事件
    await uploadBox.trigger('dragover');
    await uploadBox.trigger('dragleave');

    // 组件应该正常响应，不抛出错误
    expect(wrapper.exists()).toBe(true);
  });

  it('should display correct text for different states', () => {
    // 空状态
    expect(wrapper.text()).toContain('添加图片');

    // 有图片时的上传框
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: ['img.jpg'],
        maxImages: 3,
      },
    });

    expect(wrapper.text()).toContain('+');
  });

  it('should handle edge case: empty file list', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    Object.defineProperty(fileInput.element, 'files', {
      value: [],
      writable: false,
    });

    await fileInput.trigger('change');

    // 不应该发出更新事件
    expect(mockEmit).not.toHaveBeenCalled();
  });

  it('should handle edge case: null or undefined files', async () => {
    const fileInput = wrapper.find('input[type="file"]');

    Object.defineProperty(fileInput.element, 'files', {
      value: null,
      writable: false,
    });

    await fileInput.trigger('change');

    // 不应该抛出错误
    expect(wrapper.exists()).toBe(true);
  });
});
