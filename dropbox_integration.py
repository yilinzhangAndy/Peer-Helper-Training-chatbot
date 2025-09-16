"""
Dropbox Integration for Chatbot Logging
使用UF Dropbox存储对话数据
"""

import requests
import json
from datetime import datetime
import io
import pandas as pd

class DropboxUFLogger:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.dropboxapi.com/2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def upload_excel_file(self, session_data: dict, filename: str = None) -> bool:
        """上传Excel文件到Dropbox"""
        try:
            if not filename:
                filename = f"/Chatbot Logs/chatbot_session_{session_data.get('session_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # 准备数据
            df_data = []
            for msg in session_data.get("conversation", []):
                df_data.append({
                    "Turn": msg.get("turn", 0),
                    "Role": msg.get("role", ""),
                    "Content": msg.get("content", ""),
                    "Timestamp": msg.get("timestamp", "")
                })
            
            # 创建DataFrame
            df = pd.DataFrame(df_data)
            
            # 保存为Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Conversation', index=False)
                
                # 添加会话信息
                session_info = pd.DataFrame([{
                    "Session ID": session_data.get("session_id", ""),
                    "Persona": session_data.get("persona", ""),
                    "Message Count": session_data.get("message_count", 0),
                    "Start Time": session_data.get("start_time", ""),
                    "End Time": session_data.get("end_time", "")
                }])
                session_info.to_excel(writer, sheet_name='Session Info', index=False)
            
            excel_buffer.seek(0)
            
            # 上传到Dropbox
            upload_url = f"{self.base_url}/files/upload"
            upload_data = {
                "path": filename,
                "mode": "add",
                "autorename": True
            }
            
            response = requests.post(
                upload_url,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Dropbox-API-Arg": json.dumps(upload_data),
                    "Content-Type": "application/octet-stream"
                },
                data=excel_buffer.getvalue()
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully uploaded {filename} to Dropbox UF")
                return True
            else:
                print(f"❌ Error uploading to Dropbox: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error in Dropbox upload: {e}")
            return False
    
    def create_shared_link(self, filename: str) -> str:
        """创建共享链接"""
        try:
            share_url = f"{self.base_url}/sharing/create_shared_link_with_settings"
            share_data = {
                "path": filename,
                "settings": {
                    "requested_visibility": "public"
                }
            }
            
            response = requests.post(share_url, json=share_data, headers=self.headers)
            if response.status_code == 200:
                share_info = response.json()
                return share_info.get("url", "")
            
            return ""
            
        except Exception as e:
            print(f"❌ Error creating shared link: {e}")
            return ""

def get_dropbox_access_token():
    """获取Dropbox访问令牌的说明"""
    print("📋 Dropbox UF Access Token Setup:")
    print("=" * 50)
    print("1. 访问: https://www.dropbox.com/developers/apps")
    print("2. 使用UF账户登录")
    print("3. 创建应用程序:")
    print("   - 应用名称: Chatbot Logging")
    print("   - 应用类型: Full Dropbox")
    print("4. 获取应用程序密钥")
    print("5. 使用OAuth2流程获取访问令牌")
    print("6. 将令牌添加到Streamlit Secrets")

if __name__ == "__main__":
    get_dropbox_access_token()
