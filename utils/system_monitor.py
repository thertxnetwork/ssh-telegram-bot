"""System monitoring and statistics utilities."""
import logging

logger = logging.getLogger(__name__)


class SystemMonitor:
    """System monitoring and statistics."""
    
    @staticmethod
    def get_system_info(ssh_manager, user_id: int) -> str:
        """Get comprehensive system information."""
        commands = {
            'hostname': 'hostname',
            'os': 'cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d \\"',
            'kernel': 'uname -r',
            'uptime': 'uptime -p',
            'users': 'who | wc -l',
        }
        
        info = {}
        for key, cmd in commands.items():
            success, stdout, _ = ssh_manager.execute_command(user_id, cmd)
            info[key] = stdout.strip() if success else 'N/A'
        
        message = (
            "🖥️ **System Information**\n\n"
            f"**Hostname:** `{info['hostname']}`\n"
            f"**OS:** `{info['os']}`\n"
            f"**Kernel:** `{info['kernel']}`\n"
            f"**Uptime:** `{info['uptime']}`\n"
            f"**Users:** `{info['users']}`\n"
        )
        
        return message
    
    @staticmethod
    def get_resource_usage(ssh_manager, user_id: int) -> str:
        """Get CPU, memory, and disk usage."""
        # CPU usage
        success, cpu_out, _ = ssh_manager.execute_command(
            user_id,
            "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
        )
        cpu_usage = cpu_out.strip() if success else 'N/A'
        
        # Memory usage
        success, mem_out, _ = ssh_manager.execute_command(
            user_id,
            "free -h | awk '/^Mem:/ {print $3 \" / \" $2 \" (\" int($3/$2 * 100) \"%)\" }'"
        )
        mem_usage = mem_out.strip() if success else 'N/A'
        
        # Disk usage
        success, disk_out, _ = ssh_manager.execute_command(
            user_id,
            "df -h / | awk 'NR==2 {print $3 \" / \" $2 \" (\" $5 \")\"}'"
        )
        disk_usage = disk_out.strip() if success else 'N/A'
        
        # Load average
        success, load_out, _ = ssh_manager.execute_command(
            user_id,
            "uptime | awk -F'load average:' '{print $2}'"
        )
        load_avg = load_out.strip() if success else 'N/A'
        
        message = (
            "📊 **Resource Usage**\n\n"
            f"**CPU Usage:** `{cpu_usage}%`\n"
            f"**Memory:** `{mem_usage}`\n"
            f"**Disk (/):** `{disk_usage}`\n"
            f"**Load Average:** `{load_avg}`\n"
        )
        
        return message
    
    @staticmethod
    def get_disk_usage(ssh_manager, user_id: int) -> str:
        """Get detailed disk usage for all mounted filesystems."""
        success, stdout, _ = ssh_manager.execute_command(
            user_id,
            "df -h | grep -v tmpfs | grep -v devtmpfs"
        )
        
        if not success:
            return "❌ Could not retrieve disk usage"
        
        return f"💾 **Disk Usage**\n```\n{stdout}\n```"
    
    @staticmethod
    def get_top_processes(ssh_manager, user_id: int, limit: int = 10) -> str:
        """Get top processes by CPU/memory usage."""
        success, stdout, _ = ssh_manager.execute_command(
            user_id,
            f"ps aux --sort=-%cpu | head -n {limit + 1}"
        )
        
        if not success:
            return "❌ Could not retrieve process list"
        
        return f"⚙️ **Top {limit} Processes (by CPU)**\n```\n{stdout}\n```"
    
    @staticmethod
    def get_network_info(ssh_manager, user_id: int) -> str:
        """Get network interface information."""
        success, stdout, _ = ssh_manager.execute_command(
            user_id,
            "ip -br addr show | grep -v '^lo'"
        )
        
        if not success:
            return "❌ Could not retrieve network info"
        
        message = f"🌐 **Network Interfaces**\n```\n{stdout}\n```"
        
        # Add public IP
        success, ip_out, _ = ssh_manager.execute_command(
            user_id,
            "curl -s ifconfig.me || wget -qO- ifconfig.me"
        )
        
        if success and ip_out.strip():
            message += f"\n**Public IP:** `{ip_out.strip()}`"
        
        return message
    
    @staticmethod
    def get_listening_ports(ssh_manager, user_id: int) -> str:
        """Get listening network ports."""
        success, stdout, _ = ssh_manager.execute_command(
            user_id,
            "ss -tulnp | grep LISTEN | head -n 20"
        )
        
        if not success:
            return "❌ Could not retrieve listening ports"
        
        return f"🔌 **Listening Ports**\n```\n{stdout}\n```"
